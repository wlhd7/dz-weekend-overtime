from flask import request, render_template, make_response, redirect, url_for, jsonify
from datetime import datetime, timedelta
from .db import get_db

def init_app(app):
    @app.route('/', methods=['GET', 'POST'])
    def weekend_overtime():
        db = get_db()
        department = request.cookies.get('department', 'manu')

        # 获取日期参数
        date_str = request.args.get('date')

        if date_str:
            try:
                current_date = datetime.strptime(date_str, '%Y-%m-%d').date()
            except ValueError:
                current_date = datetime.now().date() + timedelta(days=1)
        else:
            current_date = datetime.now().date() + timedelta(days=1)

        prev_date = current_date - timedelta(days=1)
        next_date = current_date + timedelta(days=1)
        column_name = current_date.strftime('%Y_%m_%d')

        # 计算前第七天的日期
        seven_days_ago = current_date - timedelta(days=7)
        seven_days_ago_column = seven_days_ago.strftime('%Y_%m_%d')

        # 标记是否使用了备用日期
        use_fallback_date = False
        fallback_date = None
        display_date = current_date
        display_column = column_name

        if request.method == 'POST':
            # 首先检查是否是 JSON 请求
            if request.content_type and 'application/json' in request.content_type:
                try:
                    staff_data = request.get_json()
                    if not staff_data:
                        return jsonify({'success': False, 'error': '无效的JSON数据'})

                    action = staff_data.get('action')
                    print(f"Received JSON action: {action}")  # 调试信息

                    if action == 'add-date':
                        # 获取请求中的日期
                        request_date_str = staff_data.get('date')
                        if request_date_str:
                            try:
                                request_date = datetime.strptime(request_date_str, '%Y-%m-%d').date()
                                target_column = request_date.strftime('%Y_%m_%d')
                            except ValueError:
                                target_column = column_name
                        else:
                            target_column = column_name

                        # 确保目标字段存在
                        try:
                            db.execute(f'ALTER TABLE staffs ADD COLUMN "{target_column}" TEXT DEFAULT "bg-1"')
                            db.commit()
                        except Exception as e:
                            print(f"Column issue: {e}")
                            db.rollback()

                        if 'staffs' in staff_data:
                            success_count = 0
                            for staff in staff_data['staffs']:
                                try:
                                    result = db.execute(
                                        f'UPDATE staffs SET "{target_column}" = ? '
                                        'WHERE name = ? AND department = ?',
                                        (staff.get('status', 'bg-1'), staff['name'], staff['department'])
                                    )
                                    if result.rowcount > 0:
                                        success_count += 1
                                    db.commit()
                                except Exception as e:
                                    print(f"Error updating {staff['name']}: {e}")
                                    db.rollback()
                                    continue

                            print(f"Successfully updated {success_count} staff records for date {target_column}")
                            return jsonify({'success': True, 'updated': success_count, 'target_date': target_column})

                        return jsonify({'success': False, 'error': '没有员工数据'})

                except Exception as e:
                    db.rollback()
                    print(f"JSON processing error: {e}")
                    return jsonify({'success': False, 'error': str(e)}), 500

            # 处理表单请求（非JSON）
            action = request.form.get('action')
            print(f"Received form action: {action}")  # 调试信息

            if action == 'department':
                department = request.form['department']
                print(f"Changing department to: {department}")  # 调试信息
                resp = make_response(redirect(url_for('weekend_overtime', date=current_date.strftime('%Y-%m-%d'))))
                resp.set_cookie('department', department, max_age=365*24*3600)
                return resp

            elif action == 'add':
                name = request.form['name']
                sub_department = request.form.get('sub-department', 'none')

                try:
                    db.execute(
                        'INSERT OR IGNORE INTO staffs (name, department, sub_department) VALUES (?, ?, ?)',
                        (name, department, sub_department)
                    )
                    db.commit()
                except Exception as e:
                    print(f"Error adding staff: {e}")
                    db.rollback()
                return redirect(url_for('weekend_overtime', date=current_date.strftime('%Y-%m-%d')))

            elif action == 'delete':
                name = request.form['name']
                try:
                    db.execute('DELETE FROM staffs WHERE name = ?', (name,))
                    db.commit()
                except Exception as e:
                    print(f"Error deleting staff: {e}")
                    db.rollback()
                return redirect(url_for('weekend_overtime', date=current_date.strftime('%Y-%m-%d')))

        # GET 请求处理
        try:
            # 确保当前日期字段存在
            db.execute(f'ALTER TABLE staffs ADD COLUMN "{column_name}" TEXT DEFAULT "bg-1"')
            db.commit()
        except Exception as e:
            print(f"Column creation issue: {e}")

        try:
            # 确保前第七天日期字段存在
            db.execute(f'ALTER TABLE staffs ADD COLUMN "{seven_days_ago_column}" TEXT DEFAULT "bg-1"')
            db.commit()
        except Exception as e:
            print(f"Seven days ago column creation issue: {e}")

        # 检查当前日期是否有加班记录（bg-2 或 bg-3）
        has_overtime = db.execute(
            f'SELECT COUNT(*) as count FROM staffs WHERE department = ? AND ("{column_name}" = "bg-2" OR "{column_name}" = "bg-3")',
            (department,)
        ).fetchone()['count'] > 0

        # 决定使用哪个日期的数据
        if not has_overtime:
            # 检查前第七天是否有数据
            has_seven_days_data = db.execute(
                f'SELECT COUNT(*) as count FROM staffs WHERE department = ? AND ("{seven_days_ago_column}" = "bg-2" OR "{seven_days_ago_column}" = "bg-3")',
                (department,)
            ).fetchone()['count'] > 0

            if has_seven_days_data:
                display_date = seven_days_ago
                display_column = seven_days_ago_column
                use_fallback_date = True
                fallback_date = seven_days_ago

        # 获取要显示的数据
        staffs = db.execute(
            f'SELECT *, COALESCE("{display_column}", "bg-1") as current_status FROM staffs WHERE department = ?',
            (department,)
        ).fetchall()

        return render_template('weekend-overtime.html',
                             department=department,
                             staffs=staffs,
                             current_date=current_date,
                             display_date=display_date,  # 实际显示的日期
                             prev_date=prev_date,
                             next_date=next_date,
                             column_name=display_column,  # 实际使用的列名
                             use_fallback_date=use_fallback_date,
                             fallback_date=fallback_date)
